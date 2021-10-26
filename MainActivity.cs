using Android.App;
using System.Collections.Generic;
using Android.OS;
using Android.Runtime;
using Android.Widget;
using AndroidX.AppCompat.App;
using Newtonsoft.Json.Linq;
using System.Net.Http;
using System;
using Xamarin.Essentials;
using System.Net.Http.Headers;
using System.IO;
using System.Net;
using Java.Net;

namespace App1
{
    [Activity(Label = "@string/app_name", Theme = "@style/AppTheme", MainLauncher = true)]
    public class MainActivity : AppCompatActivity
    {
        int id;
        string url = "http://192.168.10.101";
        protected override void OnCreate(Bundle savedInstanceState)
        {

            TextView state = FindViewById<TextView>(Resource.Id.state_login);
            EditText in_mail = FindViewById<EditText>(Resource.Id.text_mail);
            EditText in_pass = FindViewById<EditText>(Resource.Id.text_pass);

            base.OnCreate(savedInstanceState);
            Xamarin.Essentials.Platform.Init(this, savedInstanceState);
            // Set our view from the "main" layout resource
            SetContentView(Resource.Layout.activity_main);

            //メイン画面
            this.FindViewById<Button>(Resource.Id.login_button).Click += Login_button_Click;
            this.FindViewById<Button>(Resource.Id.create).Click += Create_button_Click;
        }
        //占いの入力画面
        private void To_telling_button_Click(object sender, System.EventArgs e)
        {
            SetContentView(Resource.Layout.telling_input);
            this.FindViewById<Button>(Resource.Id.tel_back_menu).Click += To_menu_Click;
            //業務形態のプルダウン
            Spinner workclass = FindViewById<Spinner>(Resource.Id.input_workclass);
            workclass.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter1 = ArrayAdapter.CreateFromResource(this, Resource.Array.workclass_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter1.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            workclass.Adapter = adapter1;
            //最終学歴のプルダウン
            Spinner education = FindViewById<Spinner>(Resource.Id.input_education);
            education.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter2 = ArrayAdapter.CreateFromResource(this, Resource.Array.education_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter2.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            education.Adapter = adapter2;
            //属関係のプルダウン
            Spinner marital_status = FindViewById<Spinner>(Resource.Id.input_marital_status);
            marital_status.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter3 = ArrayAdapter.CreateFromResource(this, Resource.Array.marital_status_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter2.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            marital_status.Adapter = adapter3;
            //職業のプルダウン
            Spinner occupation = FindViewById<Spinner>(Resource.Id.input_occupation);
            occupation.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter4 = ArrayAdapter.CreateFromResource(this, Resource.Array.occupation_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter4.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            occupation.Adapter = adapter4;
            //家族関係のプルダウン
            Spinner relationship = FindViewById<Spinner>(Resource.Id.input_relationship);
            relationship.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter5 = ArrayAdapter.CreateFromResource(this, Resource.Array.relationship_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter5.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            relationship.Adapter = adapter5;
            //人種
            Spinner race = FindViewById<Spinner>(Resource.Id.input_race);
            race.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter6 = ArrayAdapter.CreateFromResource(this, Resource.Array.race_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter6.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            race.Adapter = adapter6;
            //性別
            Spinner sex = FindViewById<Spinner>(Resource.Id.input_sex);
            sex.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter7 = ArrayAdapter.CreateFromResource(this, Resource.Array.sex_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter7.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            sex.Adapter = adapter7;
            //母国
            Spinner native_country = FindViewById<Spinner>(Resource.Id.input_native_country);
            native_country.ItemSelected += new EventHandler<AdapterView.ItemSelectedEventArgs>(spinner_ItemSelected);
            var adapter8 = ArrayAdapter.CreateFromResource(this, Resource.Array.native_country_array, Android.Resource.Layout.SimpleSpinnerItem);
            adapter8.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
            native_country.Adapter = adapter8;
            this.FindViewById<Button>(Resource.Id.tel_result).Click += Tel_result_Click;
        }
        //プルダウン作成に必要な関数
        private void spinner_ItemSelected(object sender, AdapterView.ItemSelectedEventArgs e)
        {
            Spinner spinner = (Spinner)sender;
            string toast = string.Format("The Language is {0}", spinner.GetItemAtPosition(e.Position));
            Toast.MakeText(this, toast, ToastLength.Long).Show();
        }
        private async void Tel_result_Click(object sender, System.EventArgs e)
        {
            Button button = FindViewById<Button>(Resource.Id.tel_result);
            EditText edu_year = FindViewById<EditText>(Resource.Id.input_edu_year);
            EditText salary = FindViewById<EditText>(Resource.Id.input_salary);
            Spinner workclass = FindViewById<Spinner>(Resource.Id.input_workclass);
            Spinner education = FindViewById<Spinner>(Resource.Id.input_education);
            Spinner martial_status = FindViewById<Spinner>(Resource.Id.input_marital_status);
            Spinner occupation = FindViewById<Spinner>(Resource.Id.input_occupation);
            Spinner relationship = FindViewById<Spinner>(Resource.Id.input_relationship);
            Spinner race = FindViewById<Spinner>(Resource.Id.input_race);
            Spinner sex = FindViewById<Spinner>(Resource.Id.input_sex);
            Spinner native_country = FindViewById<Spinner>(Resource.Id.input_native_country);
            if (!string.Equals(edu_year.Text, "") && !string.Equals(salary.Text, ""))
            {
                //年収成型
                int Y;
                if (Int32.Parse(salary.Text) >= 5000000)
                {
                    Y = 1;
                }
                else
                {
                    Y = 0;
                }
                //HTTP通信
                var parameters = new JavaDictionary<string, string>
            {
                { "Y", Y.ToString()},
                { "education-num",edu_year.Text},
                { "workclass",workclass.SelectedItem.ToString()},
                { "education",education.SelectedItem.ToString()},
                { "marital-status",martial_status.SelectedItem.ToString()},
                { "occupation",occupation.SelectedItem.ToString()},
                { "relationship",relationship.SelectedItem.ToString()},
                { "race",race.SelectedItem.ToString()},
                { "sex",sex.SelectedItem.ToString()},
                { "native-country",native_country.SelectedItem.ToString()},
                { "user_id",id.ToString()}
            };
                button.Enabled = false;
                button.Text = "通信中です";
                var content = new FormUrlEncodedContent(parameters);
                //JSONの値を取得
                string jsonstr;
                try
                {
                    using (var client = new HttpClient())
                    {
                        var res = await client.PostAsync(url + ":5000/telling-ans-json", content);
                        var response = await res.Content.ReadAsStringAsync();
                        jsonstr = response;
                    }
                    JObject jsonObj = JObject.Parse(jsonstr);
                    SetContentView(Resource.Layout.telling_ans);
                    this.FindViewById<Button>(Resource.Id.telans_back_menu).Click += To_menu_Click;
                    TextView result = FindViewById<TextView>(Resource.Id.result_age);
                    result.Text = "あなたがアメリカ人だったら" + (string)jsonObj["predict"] + "歳です\n";
                }
                catch (ProtocolException)
                {
                    TextView tel_input_title = FindViewById<TextView>(Resource.Id.tel_input_title);
                    tel_input_title.Text = "通信エラー!\nやり直してください";
                    button.Text = "診断";
                    button.Enabled = true;
                }
            }
            else
            {
                TextView tel_input_title = FindViewById<TextView>(Resource.Id.tel_input_title);
                if (string.Equals(edu_year.Text, "") && string.Equals(salary.Text, ""))
                {
                    tel_input_title.Text = "教育年数と年収を入れてください";
                }
                else if (string.Equals(edu_year.Text, ""))
                {
                    tel_input_title.Text = "教育年数を入れてください";
                }
                else
                {
                    tel_input_title.Text = "年収を入れてください";
                }
            }
        }

        //メニュー画面
        private void To_menu_Click(object sender, System.EventArgs e)
        {
            SetContentView(Resource.Layout.menu_con);
            this.FindViewById<Button>(Resource.Id.to_image).Click += To_image_button_Click;
            this.FindViewById<Button>(Resource.Id.to_telling).Click += To_telling_button_Click;
            this.FindViewById<Button>(Resource.Id.to_analysis).Click += To_anakysis_button_Click;
        }


        //統計データ送信画面
        private void To_anakysis_button_Click(object sender, System.EventArgs e)
        {
            SetContentView(Resource.Layout.stat_sed);
            this.FindViewById<Button>(Resource.Id.stat_back_menu).Click += To_menu_Click;
            this.FindViewById<Button>(Resource.Id.stat_select).Click += To_customstat_Click;
        }

        //統計データ選択
        private async void To_customstat_Click(object sender, EventArgs e)
        {
            Button stat_select = FindViewById<Button>(Resource.Id.stat_select);
            TextView stat_send_title = FindViewById<TextView>(Resource.Id.stat_send_title);
            var file = await FilePicker.PickAsync();
            if (string.Equals(System.IO.Path.GetExtension(file.FullPath.ToString()), ".csv"))
            {
                //パラメータ作り
                var parameters = new JavaDictionary<string, string>
            {
                { "user_id",id.ToString()},
            };
                var content = new MultipartFormDataContent();

                var fileContent = new StreamContent(System.IO.File.OpenRead(file.FullPath));
                fileContent.Headers.ContentDisposition = new ContentDispositionHeaderValue("attachment")
                {
                    FileName = Path.GetFileName(file.FullPath),
                    Name = "stat"
                };
                foreach (var param in parameters)
                {
                    content.Add(new StringContent(param.Value), param.Key);
                }
                content.Add(fileContent);
                //HTTP通信
                stat_select.Enabled = false;
                stat_select.Text = "送信中";
                var client = new HttpClient();
                try
                {
                    var res = await client.PostAsync(url + ":5000/stat-before-json", content);
                    var response = await res.Content.ReadAsStringAsync();
                    Console.WriteLine("OK");
                    JArray jsonObj = JArray.Parse(response);
                    SetContentView(Resource.Layout.stat_arange);
                    this.FindViewById<Button>(Resource.Id.stat_arange_back_menu).Click += To_menu_Click;
                    //数値とカテゴリ選択
                    var rc = new List<string>();
                    rc.Add("数値");
                    rc.Add("カテゴリ");
                    Spinner reg_cla = FindViewById<Spinner>(Resource.Id.stat_arange_reg_cla);
                    ArrayAdapter adapter1 = new ArrayAdapter(this, Android.Resource.Layout.SimpleSpinnerItem, rc);
                    adapter1.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
                    reg_cla.Adapter = adapter1;
                    TextView stat_arange_title = FindViewById<TextView>(Resource.Id.stat_arange_title);
                    //目的変数の選択
                    stat_arange_title.Text = (string)jsonObj[0]["name"];
                    JObject col = JObject.Parse(jsonObj[1].ToString());
                    var columns = new List<string>();
                    foreach (var json in col)
                    {
                        columns.Add(json.Key);
                    }
                    Spinner y = FindViewById<Spinner>(Resource.Id.stat_arange_y);
                    ArrayAdapter adapter2 = new ArrayAdapter(this, Android.Resource.Layout.SimpleSpinnerItem, columns);
                    adapter2.SetDropDownViewResource(Android.Resource.Layout.SimpleSpinnerDropDownItem);
                    y.Adapter = adapter2;
                    Spinner stat_arange_cate = FindViewById<Spinner>(Resource.Id.stat_arange_cate);
                    stat_arange_cate.Adapter = adapter2;
                    //選択
                    this.FindViewById<Button>(Resource.Id.stat_arange_select_cate).Click += To_cate_select_Click;
                    //送信
                    this.FindViewById<Button>(Resource.Id.stat_arange_to_result).Click += To_stat_result_Click;
                }
                catch (ProtocolException)
                {
                    stat_send_title.Text = "送信エラーが発生\nやり直してください";
                    stat_select.Text = "選択";
                    stat_select.Enabled = true;
                }
            }
            else 
            {
                stat_send_title.Text = "CSVファイルを選んでください";
            }
        }

        //カテゴリ変数選択
        private void To_cate_select_Click(object sender, EventArgs e)
        {
            this.FindViewById<Button>(Resource.Id.stat_arange_to_result).Click += To_stat_result_Click;
            this.FindViewById<Button>(Resource.Id.stat_arange_back_menu).Click += To_menu_Click;
            EditText selected_category = FindViewById<EditText>(Resource.Id.selected_category);
            Spinner stat_arange_cate = FindViewById<Spinner>(Resource.Id.stat_arange_cate);
            Spinner stat_arange_y = FindViewById<Spinner>(Resource.Id.stat_arange_y);
            if (string.Equals(selected_category.Text, ""))
            {
                if (!string.Equals(stat_arange_y.SelectedItem.ToString(), stat_arange_cate.SelectedItem.ToString()))
                {
                    selected_category.Text = stat_arange_cate.SelectedItem.ToString();
                }
            }
            else
            {
                if (!selected_category.Text.Contains(stat_arange_cate.SelectedItem.ToString()))
                {
                    if (!string.Equals(stat_arange_y.SelectedItem.ToString(),stat_arange_cate.SelectedItem.ToString())) 
                    {
                        selected_category.Text = selected_category.Text + "," + stat_arange_cate.SelectedItem.ToString();
                    }
                }
            }
        }

        //データ送信画面
        private async void To_stat_result_Click(object sender, EventArgs e)
        {
            this.FindViewById<Button>(Resource.Id.stat_arange_back_menu).Click += To_menu_Click;
            Spinner Y = FindViewById<Spinner>(Resource.Id.stat_arange_reg_cla);//数値かカテゴリか
            Spinner y = FindViewById<Spinner>(Resource.Id.stat_arange_y);//目的変数
            TextView stat_arange_title = FindViewById<TextView>(Resource.Id.stat_arange_title);
            EditText selected_category = FindViewById<EditText>(Resource.Id.selected_category);
            Spinner reg_cla = FindViewById<Spinner>(Resource.Id.stat_arange_reg_cla);
            Button stat_arange_to_result = FindViewById<Button>(Resource.Id.stat_arange_to_result);
            TextView stat_arange_msg_error = FindViewById<TextView>(Resource.Id.stat_arange_msg_error);
            string yk;
            if (!selected_category.Text.Contains(y.SelectedItem.ToString()))
            {
                if (string.Equals(Y.SelectedItem.ToString(), "数値"))
                {
                    yk = "reg";
                }
                else
                {
                    yk = "cla";
                }
                //URIパラメータ作り
                var parameters = new JavaDictionary<string, string>
                {
                    { "yk", yk},
                    { "y",y.SelectedItem.ToString()},
                    { "cate","["+selected_category.Text+"]"},
                    { "name",stat_arange_title.Text},
                    { "user_id",id.ToString()}
                };
                var content = new FormUrlEncodedContent(parameters);
                //HTTP通信
                string jsonstr;
                var client = new HttpClient();
                
                try
                {
                    stat_arange_to_result.Enabled = false;
                    stat_arange_to_result.Text = "送信中";
                    var res = await client.PostAsync(url + ":5000/stat-json", content);
                    var response = await res.Content.ReadAsStringAsync();
                    jsonstr = response;

                    //JSON作成
                    JArray jsonObj = JArray.Parse(jsonstr);
                    SetContentView(Resource.Layout.stat_result);
                    this.FindViewById<Button>(Resource.Id.stat_result_back_menu).Click += To_menu_Click;
                    TextView stat_result_msg = FindViewById<TextView>(Resource.Id.stat_result_msg);
                    if (string.Equals(yk, "cla"))
                    {
                        for (int i = 0; i < jsonObj.Count; i++)
                        {
                            try
                            {
                                JObject json = JObject.Parse(jsonObj[i].ToString());
                                stat_result_msg.Text = stat_result_msg.Text + "\n項目名：" + json["col"] + "\n影響度：" + json["imp"].ToString() + "%\n";
                            }
                            catch
                            {
                                break;
                            }
                        }
                    }
                    else if (string.Equals(yk, "reg"))
                    {
                        for (int i = 0; i < jsonObj.Count; i++)
                        {
                            try
                            {
                                JObject json = JObject.Parse(jsonObj[i].ToString());
                                stat_result_msg.Text = stat_result_msg.Text + "\n　項目名：" + json["col"] + "\n　影響度：" + json["imp"].ToString() + "%\n相関係数：" + json["cor"].ToString() + "\n";
                            }
                            catch
                            {
                                break;
                            }
                        }
                    }
                }
                catch (ProtocolException)
                {
                    stat_arange_to_result.Text = "分析";
                    stat_arange_to_result.Enabled = true;
                    stat_arange_msg_error.Text = "通信でエラーが発生\nやり直してください";
                }
            }
            else {
                stat_arange_msg_error.Text = "カテゴリ一覧に目的変数が含まれています";
            }
        }


        //画像データ送信画面
        private void To_image_button_Click(object sender, System.EventArgs e)
        {
            SetContentView(Resource.Layout.image_send);
            this.FindViewById<Button>(Resource.Id.img_back_menu).Click += To_menu_Click;
            TextView user_id = FindViewById<TextView>(Resource.Id.img_user_id);
            this.FindViewById<Button>(Resource.Id.select_img).Click += To_select_img_Click;
        }

        private async void To_select_img_Click(object sender, EventArgs e)
        {
            Button img_send = FindViewById<Button>(Resource.Id.select_img);
            var file = await FilePicker.PickAsync(new PickOptions
            {
                PickerTitle = "Select the image",
                FileTypes = FilePickerFileType.Images
            });

            //パラメータ作り
            var parameters = new JavaDictionary<string, string>
            {
                { "user_id",id.ToString()},
            };
            var content = new MultipartFormDataContent();

            var fileContent = new StreamContent(System.IO.File.OpenRead(file.FullPath));
            fileContent.Headers.ContentDisposition = new ContentDispositionHeaderValue("attachment")
            {
                FileName = Path.GetFileName(file.FullPath),
                Name = "img"
            };
            foreach (var param in parameters)
            {
                content.Add(new StringContent(param.Value), param.Key);
            }
            content.Add(fileContent);

            //HTTP通信
            img_send.Enabled = false;
            img_send.Text = "送信中";
            var client = new HttpClient();
            try
            {
                var res = await client.PostAsync(url + ":5000/image-result-json", content);
                var response = await res.Content.ReadAsStringAsync();
                JObject jsonObj = JObject.Parse(response);
                SetContentView(Resource.Layout.image_result);
                this.FindViewById<Button>(Resource.Id.img_result_back_menu).Click += To_menu_Click;
                TextView img_result = FindViewById<TextView>(Resource.Id.img_result);
                for (int i = 1; i <= 10; i++)
                {
                    img_result.Text = img_result.Text + "\n\n" + i.ToString() + "位\n候補名：" + jsonObj[i.ToString()]["name"] + "\n確　率：" + jsonObj[i.ToString()]["proba"] + "%";
                }
            }
            catch (ProtocolException)
            {
                TextView img_send_title = FindViewById<TextView>(Resource.Id.img_send_title);
                img_send_title.Text = "通信エラー！\nやり直してください";
                img_send.Text = "画像選択";
                img_send.Enabled = true;
            }
        }



        private async void Create_button_Click(object sender, System.EventArgs e)
        {
            TextView state = FindViewById<TextView>(Resource.Id.state_login);
            TextView id_num = FindViewById<TextView>(Resource.Id.id_num);
            EditText in_mail = FindViewById<EditText>(Resource.Id.text_mail);
            EditText in_pass = FindViewById<EditText>(Resource.Id.text_pass);
            Button create = FindViewById<Button>(Resource.Id.create);
            Button login_button = FindViewById<Button>(Resource.Id.login_button);

            //HTTP通信
            var parameters = new JavaDictionary<string, string>
            {
                { "name",in_mail.Text},
                { "pass",in_pass.Text},
            };
            var content = new FormUrlEncodedContent(parameters);
            //JSONの値を取得
            string jsonstr;
            try
            {
                login_button.Enabled = false;
                create.Enabled = false;
                create.Text = "送信中";
                using (var client = new HttpClient())
                {
                    var res = await client.PostAsync(url + ":5000/create-json", content);
                    var response = await res.Content.ReadAsStringAsync();
                    jsonstr = response;
                }
                JObject jsonObj = JObject.Parse(jsonstr);

                //0ならこのページ
                if ((int)jsonObj["id"] == 0)
                {
                    create.Text = "新規登録";
                    login_button.Enabled = true;
                    create.Enabled = true;
                    state.Text = (string)jsonObj["result"];
                }

                //idを取得出来たらメニューページ
                else
                {
                    id_num.Text = (string)jsonObj["id"];
                    id = (int)jsonObj["id"];
                    SetContentView(Resource.Layout.menu_con);
                    //メニュー画面
                    this.FindViewById<Button>(Resource.Id.to_image).Click += To_image_button_Click;
                    this.FindViewById<Button>(Resource.Id.to_telling).Click += To_telling_button_Click;
                    this.FindViewById<Button>(Resource.Id.to_analysis).Click += To_anakysis_button_Click;
                }
            }
            catch (ProtocolException)
            {
                create.Text = "新規登録";
                login_button.Enabled = true;
                create.Enabled = true;
                state.Text = "通信でエラーが発生!やり直してください";
            }
        }

        private async void Login_button_Click(object sender, System.EventArgs e)
        {
            TextView state = FindViewById<TextView>(Resource.Id.state_login);
            TextView id_num = FindViewById<TextView>(Resource.Id.id_num);
            EditText in_mail = FindViewById<EditText>(Resource.Id.text_mail);
            EditText in_pass = FindViewById<EditText>(Resource.Id.text_pass);
            Button create = FindViewById<Button>(Resource.Id.create);
            Button login_button = FindViewById<Button>(Resource.Id.login_button);

            //HTTP通信
            var parameters = new JavaDictionary<string, string>
            {
                { "name",in_mail.Text},
                { "pass",in_pass.Text},
            };
            var content = new FormUrlEncodedContent(parameters);
            //JSONの値を取得
            string jsonstr;
            try
            {
                login_button.Enabled = false;
                create.Enabled = false;
                login_button.Text = "送信中";
                using (var client = new HttpClient())
                {
                    var res = await client.PostAsync(url + ":5000/login-json", content);
                    var response = await res.Content.ReadAsStringAsync();
                    jsonstr = response;
                }
                JObject jsonObj = JObject.Parse(jsonstr);

                //0ならこのページ
                if ((int)jsonObj["id"] == 0)
                {
                    login_button.Text = "ログイン";
                    login_button.Enabled = true;
                    create.Enabled = true;
                    state.Text = "メールアドレスかパスワードが間違っています";
                }

                //idを取得出来たらメニューページ
                else
                {
                    id_num.Text = (string)jsonObj["id"];
                    id = (int)jsonObj["id"];
                    SetContentView(Resource.Layout.menu_con);
                    //メニュー画面
                    this.FindViewById<Button>(Resource.Id.to_image).Click += To_image_button_Click;
                    this.FindViewById<Button>(Resource.Id.to_telling).Click += To_telling_button_Click;
                    this.FindViewById<Button>(Resource.Id.to_analysis).Click += To_anakysis_button_Click;

                }
            }
            catch (ProtocolException)
            {
                login_button.Text = "ログイン";
                login_button.Enabled = true;
                create.Enabled = true;
                state.Text = "通信でエラーが発生!やり直してください";
            }
        }

        public override void OnRequestPermissionsResult(int requestCode, string[] permissions, [GeneratedEnum] Android.Content.PM.Permission[] grantResults)
        {
            Xamarin.Essentials.Platform.OnRequestPermissionsResult(requestCode, permissions, grantResults);

            base.OnRequestPermissionsResult(requestCode, permissions, grantResults);
        }
    }
}
